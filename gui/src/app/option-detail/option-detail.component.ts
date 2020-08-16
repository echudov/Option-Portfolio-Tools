import { Component, OnInit } from '@angular/core';
import { Security } from '../security'

@Component({
  selector: 'app-option-detail',
  templateUrl: './option-detail.component.html',
  styleUrls: ['./option-detail.component.css']
})
export class OptionDetailComponent implements OnInit {
  security: Security = {
    ticker: 'AMD',
    security_type: 'put',
    strike: 65,
    weight: 0.5,
    expiry: Date("2020-09-20")
  }
  constructor() { }

  ngOnInit(): void {
  }

}
