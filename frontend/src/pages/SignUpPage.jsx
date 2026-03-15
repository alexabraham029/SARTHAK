import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { Scale } from 'lucide-react';

const SignUpPage = () => {
  return (
    <div className="app-background min-h-screen flex items-center justify-center px-4">
      <div className="flex flex-col items-center gap-8">
        {/* Branding */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/25">
            <Scale className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Sarthak</h1>
            <p className="text-[11px] font-medium tracking-wider uppercase text-white/40">
              AI Legal Assistant
            </p>
          </div>
        </div>

        {/* Clerk Sign-Up */}
        <SignUp
          routing="path"
          path="/sign-up"
          signInUrl="/sign-in"
          afterSignUpUrl="/"
          appearance={{
            elements: {
              rootBox: 'w-full max-w-md',
              card: 'glass-card !bg-[rgba(255,255,255,0.06)] !border-[rgba(255,255,255,0.1)] !shadow-[0_8px_32px_rgba(0,0,0,0.3)] !rounded-2xl',
              headerTitle: '!text-white !font-bold',
              headerSubtitle: '!text-white/50',
              socialButtonsBlockButton:
                '!bg-[rgba(255,255,255,0.08)] !border-[rgba(255,255,255,0.12)] !text-white hover:!bg-[rgba(255,255,255,0.14)] !rounded-xl !transition-all',
              socialButtonsBlockButtonText: '!text-white/80',
              dividerLine: '!bg-white/10',
              dividerText: '!text-white/30',
              formFieldLabel: '!text-white/60',
              formFieldInput:
                '!bg-[rgba(255,255,255,0.06)] !border-[rgba(255,255,255,0.1)] !text-white !rounded-xl focus:!border-amber-500/50 focus:!shadow-[0_0_20px_rgba(245,158,11,0.15)] !placeholder-white/35',
              formButtonPrimary:
                '!bg-gradient-to-r !from-amber-500 !to-amber-600 hover:!shadow-[0_6px_25px_rgba(245,158,11,0.5)] !rounded-xl !font-semibold !transition-all !border-none',
              footerActionLink: '!text-amber-400 hover:!text-amber-300',
              footerActionText: '!text-white/40',
              identityPreviewEditButton: '!text-amber-400',
              formFieldAction: '!text-amber-400',
              otpCodeFieldInput:
                '!bg-[rgba(255,255,255,0.06)] !border-[rgba(255,255,255,0.1)] !text-white !rounded-lg',
              phoneInputBox:
                '!bg-[rgba(255,255,255,0.06)] !border-[rgba(255,255,255,0.1)] !rounded-xl',
              formFieldPhoneInput: '!text-white',
              selectButton:
                '!bg-[rgba(255,255,255,0.08)] !border-[rgba(255,255,255,0.1)] !text-white/70 !rounded-lg',
              selectSearchInput:
                '!bg-[rgba(255,255,255,0.06)] !border-[rgba(255,255,255,0.1)] !text-white !rounded-lg',
              selectOptionsContainer:
                '!bg-[rgba(20,20,50,0.95)] !border-[rgba(255,255,255,0.1)] !rounded-xl',
              selectOption: '!text-white/70 hover:!bg-white/10',
              selectOption__active: '!text-amber-400',
              alternativeMethodsBlockButton:
                '!text-white/60 !border-[rgba(255,255,255,0.1)] hover:!bg-[rgba(255,255,255,0.08)] !rounded-xl',
              alertText: '!text-white/70',
              formFieldErrorText: '!text-red-400',
              formFieldSuccessText: '!text-emerald-400',
              identityPreviewText: '!text-white/70',
              formHeaderTitle: '!text-white',
              formHeaderSubtitle: '!text-white/50',
              backLink: '!text-amber-400 hover:!text-amber-300',
              internal: '',
            },
          }}
        />
      </div>
    </div>
  );
};

export default SignUpPage;
