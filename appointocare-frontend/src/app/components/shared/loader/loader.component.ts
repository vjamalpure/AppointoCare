import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loader',
  template: `
    <div class="loader-container" *ngIf="loading">
      <mat-spinner [diameter]="diameter"></mat-spinner>
      <p class="loading-text" *ngIf="message">{{ message }}</p>
    </div>
  `,
  styles: [`
    .loader-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      gap: 12px;
    }
    .loading-text {
      color: #64748b;
      font-size: 14px;
      margin: 0;
    }
  `]
})
export class LoaderComponent {
  @Input() loading = true;
  @Input() diameter = 40;
  @Input() message = '';
}
