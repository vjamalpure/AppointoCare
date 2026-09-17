import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-whatsapp-chat',
  templateUrl: './whatsapp-chat.component.html',
  styleUrls: ['./whatsapp-chat.component.scss']
})
export class WhatsAppChatComponent implements OnInit {
  @ViewChild('chatScroll') private chatScrollContainer!: ElementRef;

  config: any = null;
  logs: any[] = [];
  loading = false;
  sendingDirect = false;
  simulating = false;

  // Bot Simulator State
  botState = 'MENU_CHOICE';
  chatHistory: { sender: 'user' | 'bot'; text: string; time: string }[] = [
    {
      sender: 'user',
      text: 'Hi',
      time: '10:14 AM'
    },
    {
      sender: 'bot',
      text: '👋 Hello Eleanor Vance! Welcome to *City Care Health & Dental*.\n\nPlease select an option by replying with a number:\n\n1️⃣ *Book Appointment*\n2️⃣ *View My Appointments*\n3️⃣ *Cancel an Appointment*\n4️⃣ *Pay Pending Invoice Online*\n5️⃣ *Connect to Support Representative*',
      time: '10:14 AM'
    }
  ];

  userInput = '';
  simulatedPhone = '+1 555-0199';
  simulatedName = 'Eleanor Vance';

  // Direct Message Drawer/Form
  directMessage = {
    recipient_name: '',
    recipient_phone: '+1 ',
    template: 'appointment_reminder',
    custom_text: 'Hello, this is a friendly reminder for your upcoming dental checkup tomorrow at 2:30 PM. Reply 1 to confirm.'
  };

  templates = [
    { id: 'appointment_reminder', name: 'Appointment Reminder (24h prior)', text: 'Hello, this is a friendly reminder for your upcoming dental checkup tomorrow at 2:30 PM. Reply 1 to confirm.' },
    { id: 'payment_link', name: 'Razorpay Invoice Payment Link', text: 'Hi, your invoice of $85.00 for Dental Cleaning is ready. Secure link: https://appointo.core/pay/live?order=rzp_9901' },
    { id: 'feedback_request', name: 'Post-Visit Feedback Survey', text: 'Thank you for visiting City Care! How was your appointment today with Dr. Sarah? Rate us from 1 (Poor) to 5 (Excellent).' }
  ];

  constructor(
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.platform.getWhatsAppConfig().subscribe(cfg => this.config = cfg);
    this.platform.getWhatsAppLogs().subscribe(logs => {
      this.logs = logs;
      this.loading = false;
    });
  }

  sendSimulatedMessage(presetText?: string): void {
    const textToSend = presetText || this.userInput;
    if (!textToSend.trim()) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    this.chatHistory.push({
      sender: 'user',
      text: textToSend,
      time: timeStr
    });
    this.userInput = '';
    this.scrollToBottom();

    this.simulating = true;
    this.platform.simulateWhatsAppChat({
      message: textToSend,
      phone: this.simulatedPhone,
      sender_name: this.simulatedName,
      state: this.botState
    }).subscribe({
      next: (res) => {
        this.simulating = false;
        this.botState = res.nextState || 'IDLE';
        this.chatHistory.push({
          sender: 'bot',
          text: res.reply,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
        this.scrollToBottom();
        // Refresh logs and quota count
        this.platform.getWhatsAppLogs().subscribe(l => this.logs = l);
        this.platform.getWhatsAppConfig().subscribe(c => this.config = c);
      },
      error: () => {
        this.simulating = false;
        this.snackBar.open('Bot simulator communication failed', 'Dismiss', { duration: 2500 });
      }
    });
  }

  sendDirectCampaign(): void {
    if (!this.directMessage.recipient_phone || !this.directMessage.custom_text) {
      this.snackBar.open('Please specify recipient phone and message', 'Dismiss', { duration: 2500 });
      return;
    }

    this.sendingDirect = true;
    this.platform.sendWhatsAppMessage({
      recipient_number: this.directMessage.recipient_phone,
      recipient_name: this.directMessage.recipient_name || 'Valued Client',
      message: this.directMessage.custom_text,
      message_type: this.directMessage.template
    }).subscribe({
      next: () => {
        this.sendingDirect = false;
        this.snackBar.open('WhatsApp broadcast dispatched via Meta Cloud API!', 'Dismiss', { duration: 3000 });
        this.directMessage.custom_text = '';
        this.loadData();
      },
      error: () => {
        this.sendingDirect = false;
        this.snackBar.open('Failed to send WhatsApp message', 'Dismiss', { duration: 3000 });
      }
    });
  }

  onTemplateChange(tmplId: string): void {
    const found = this.templates.find(t => t.id === tmplId);
    if (found) {
      this.directMessage.custom_text = found.text;
    }
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatScrollContainer) {
        this.chatScrollContainer.nativeElement.scrollTop = this.chatScrollContainer.nativeElement.scrollHeight;
      }
    }, 100);
  }
}
