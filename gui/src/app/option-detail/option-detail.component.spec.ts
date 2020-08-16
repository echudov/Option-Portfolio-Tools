import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OptionDetailComponent } from './option-detail.component';

describe('OptionDetailComponent', () => {
  let component: OptionDetailComponent;
  let fixture: ComponentFixture<OptionDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OptionDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OptionDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
