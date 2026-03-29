import { Component, Input, Output, EventEmitter } from '@angular/core';
 
@Component({
  selector: 'app-aide-exo',
  imports: [],
  templateUrl: './aide-exo.html',
  styleUrl: './aide-exo.css',
})
export class AideExo {
  @Input() isOpen = false;
  @Output() isOpenChange = new EventEmitter<boolean>();
 
  close() {
    this.isOpenChange.emit(false);
  }
}
 