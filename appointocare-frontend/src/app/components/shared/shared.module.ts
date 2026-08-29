import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { SidebarComponent } from './sidebar/sidebar.component';
import { FooterComponent } from './footer/footer.component';
import { LoaderComponent } from './loader/loader.component';
import { ToolbarComponent } from './toolbar/toolbar.component';

@NgModule({
  declarations: [
    SidebarComponent,
    FooterComponent,
    LoaderComponent,
    ToolbarComponent
  ],
  imports: [
    CommonModule,
    RouterModule   // ✅ Needed for routerLink
  ],
  exports: [
    SidebarComponent,
    FooterComponent,
    LoaderComponent,
    ToolbarComponent
  ]
})
export class SharedModule {}
