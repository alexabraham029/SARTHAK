import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useClerk, useSignUp } from '@clerk/clerk-react';
import { Chrome, Scale, Sparkles } from 'lucide-react';

const SignUpPage = () => {
  const navigate = useNavigate();
  const { setActive } = useClerk();
  const { isLoaded, signUp } = useSignUp();
  const [emailAddress, setEmailAddress] = useState('');
  const [password, setPassword] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [pendingVerification, setPendingVerification] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const onGoogleSignUp = async () => {
    if (!isLoaded || isSubmitting || pendingVerification) return;

    try {
      setError('');
      setIsSubmitting(true);

      await signUp.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/sso-callback',
        redirectUrlComplete: '/',
      });
    } catch (err) {
      setError(err?.errors?.[0]?.message || 'Unable to continue with Google. Please try again.');
      setIsSubmitting(false);
    }
  };

  const onSignUp = async (event) => {
    event.preventDefault();
    if (!isLoaded || isSubmitting) return;

    try {
      setError('');
      setIsSubmitting(true);

      await signUp.create({
        emailAddress,
        password,
      });

      await signUp.prepareEmailAddressVerification({
        strategy: 'email_code',
      });

      setPendingVerification(true);
    } catch (err) {
      setError(err?.errors?.[0]?.message || 'Unable to create account. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onVerify = async (event) => {
    event.preventDefault();
    if (!isLoaded || isSubmitting) return;

    try {
      setError('');
      setIsSubmitting(true);

      const result = await signUp.attemptEmailAddressVerification({
        code: verificationCode.trim(),
      });

      if (result.status === 'complete' && result.createdSessionId) {
        await setActive({ session: result.createdSessionId });
        navigate('/', { replace: true });
        return;
      }

      if (result.status === 'complete' && !result.createdSessionId) {
        setError('Email verified, but no session was created. Please sign in once.');
        navigate('/sign-in', { replace: true });
        return;
      }

      if (result.status === 'missing_requirements') {
        const missingFields = Array.isArray(result.missingFields) ? result.missingFields.join(', ') : null;
        setError(
          missingFields
            ? `Email verified. Please complete required fields: ${missingFields}.`
            : 'Email verified, but additional account details are required in Clerk settings.',
        );
        return;
      }

      setError('Verification succeeded but account setup is incomplete. Please try signing in.');
    } catch (err) {
      setError(err?.errors?.[0]?.message || 'Invalid verification code. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-background min-h-screen flex items-center justify-center px-4 py-8">
      <div className="flex flex-col items-center gap-6 w-full max-w-md">
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

        <div className="w-full glass-card bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] shadow-[0_8px_32px_rgba(0,0,0,0.3)] rounded-2xl p-8">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-4 text-[11px] font-medium tracking-wider uppercase glass-card-sm text-amber-400">
            <Sparkles className="w-3 h-3" />
            Fast Onboarding
          </div>
          <h2 className="text-white text-2xl font-bold text-center">
            {pendingVerification ? 'Verify your email' : 'Create account'}
          </h2>
          <p className="text-white/50 text-sm text-center mt-1">
            {pendingVerification ? 'Enter the code sent to your email' : 'Sign up with email and password'}
          </p>

          {!pendingVerification ? (
            <>
              <button
                type="button"
                onClick={onGoogleSignUp}
                disabled={!isLoaded || isSubmitting}
                className="w-full mt-6 py-3 rounded-xl font-semibold transition-all border border-white/15 bg-white/5 hover:bg-white/10 text-white disabled:opacity-70 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
              >
                <Chrome className="w-4 h-4" />
                Continue with Google
              </button>

              <div className="my-5 flex items-center gap-3 text-xs uppercase tracking-wider text-white/35">
                <div className="h-px flex-1 bg-white/10" />
                or
                <div className="h-px flex-1 bg-white/10" />
              </div>
            </>
          ) : null}

          {!pendingVerification ? (
            <form onSubmit={onSignUp} className="space-y-4">
              <div>
                <label className="block text-white/60 text-sm mb-2">Email</label>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(event) => setEmailAddress(event.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] text-white rounded-xl focus:outline-none focus:border-amber-500/50 focus:shadow-[0_0_20px_rgba(245,158,11,0.15)] placeholder-white/35"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label className="block text-white/60 text-sm mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] text-white rounded-xl focus:outline-none focus:border-amber-500/50 focus:shadow-[0_0_20px_rgba(245,158,11,0.15)] placeholder-white/35"
                  placeholder="Create a password"
                />
              </div>

              {error ? <p className="text-red-400 text-sm">{error}</p> : null}

              <button
                type="submit"
                disabled={!isLoaded || isSubmitting}
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:shadow-[0_6px_25px_rgba(245,158,11,0.5)] rounded-xl font-semibold text-white transition-all border-none disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Creating account...' : 'Create account'}
              </button>
            </form>
          ) : (
            <form onSubmit={onVerify} className="mt-6 space-y-4">
              <div>
                <label className="block text-white/60 text-sm mb-2">Verification code</label>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(event) => setVerificationCode(event.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] text-white rounded-xl focus:outline-none focus:border-amber-500/50 focus:shadow-[0_0_20px_rgba(245,158,11,0.15)] placeholder-white/35"
                  placeholder="Enter code"
                />
              </div>

              {error ? <p className="text-red-400 text-sm">{error}</p> : null}

              <button
                type="submit"
                disabled={!isLoaded || isSubmitting}
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:shadow-[0_6px_25px_rgba(245,158,11,0.5)] rounded-xl font-semibold text-white transition-all border-none disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Verifying...' : 'Verify and continue'}
              </button>
            </form>
          )}

          <p className="text-white/40 text-sm text-center mt-5">
            Already have an account?{' '}
            <Link to="/sign-in" className="text-amber-400 hover:text-amber-300">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
