import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { IndustryService } from '../../services/industry.service';
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

  // Multi-Industry Engine
  sector = 'Healthcare';
  terms: any;
  industryConfig: any;
  whatsappDefaults: any;

  // Bot Simulator State
  botState = 'MENU_CHOICE';
  chatHistory: { sender: 'user' | 'bot'; text: string; time: string }[] = [];

  userInput = '';
  simulatedPhone = '+1 555-0199';
  simulatedName = 'Eleanor Vance';

  // Direct Message Drawer/Form
  directMessage = {
    recipient_name: '',
    recipient_phone: '+1 ',
    template: 'appointment_reminder',
    custom_text: ''
  };

  templates: { id: string; name: string; text: string }[] = [];

  constructor(
    private platform: PlatformService,
    public industryService: IndustryService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.sector = this.industryService.getSector();
    this.terms = this.industryService.getTerms(this.sector);
    this.industryConfig = this.industryService.getConfig(this.sector);
    this.whatsappDefaults = this.industryService.getWhatsAppDefaults(this.sector);

    // Dynamic initial chatbot history
    this.chatHistory = [
      {
        sender: 'user',
        text: 'Hi',
        time: '10:14 AM'
      },
      {
        sender: 'bot',
        text: this.whatsappDefaults.welcomeMessage.replace('{customer_name}', this.simulatedName),
        time: '10:14 AM'
      }
    ];

    // Dynamic templates
    this.templates = [
      {
        id: 'appointment_reminder',
        name: `${this.terms.appointmentLabel} Reminder (24h prior)`,
        text: this.industryConfig.defaultWhatsAppTemplate
      },
      {
        id: 'payment_link',
        name: 'Razorpay Invoice & Fee Link',
        text: `Hi {customer_name}, your invoice for ${this.terms.serviceLabel} is ready. Secure online checkout: https://appointocare.app/pay?order=rzp_${Date.now().toString().slice(-4)}`
      },
      {
        id: 'feedback_request',
        name: 'Post-Visit Feedback & NPS Survey',
        text: `Thank you for visiting! How was your experience today with your ${this.terms.staffLabel.toLowerCase()}? Rate us from 1 (Poor) to 5 (Excellent).`
      }
    ];

    this.directMessage.custom_text = this.templates[0].text;
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
        this.platform.getWhatsAppLogs().subscribe(l => this.logs = l);
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
