import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from '../../material.module';

import { SidebarComponent } from './sidebar/sidebar.component';
import { FooterComponent } from './footer/footer.component';
import { LoaderComponent } from './loader/loader.component';
import { ToolbarComponent } from './toolbar/toolbar.component';
import { NotificationsCenterComponent } from '../notifications/notifications-center.component';

@NgModule({
  declarations: [
    SidebarComponent,
    FooterComponent,
    LoaderComponent,
    ToolbarComponent,
    NotificationsCenterComponent
  ],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MaterialModule
  ],
  exports: [
    SidebarComponent,
    FooterComponent,
    LoaderComponent,
    ToolbarComponent,
    NotificationsCenterComponent
  ]
})
export class SharedModule {}
