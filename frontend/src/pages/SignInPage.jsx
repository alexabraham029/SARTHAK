import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useClerk, useSignIn } from '@clerk/clerk-react';
import { Scale } from 'lucide-react';

const SignInPage = () => {
  const navigate = useNavigate();
  const { setActive } = useClerk();
  const { isLoaded, signIn } = useSignIn();
  const [emailAddress, setEmailAddress] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!isLoaded || isSubmitting) return;

    try {
      setError('');
      setIsSubmitting(true);

      const result = await signIn.create({
        identifier: emailAddress,
        password,
      });

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId });
        navigate('/');
      }
    } catch (err) {
      setError(err?.errors?.[0]?.message || 'Unable to sign in. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

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

        <div className="w-full max-w-md glass-card bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] shadow-[0_8px_32px_rgba(0,0,0,0.3)] rounded-2xl p-8">
          <h2 className="text-white text-2xl font-bold text-center">Sign in</h2>
          <p className="text-white/50 text-sm text-center mt-1">Use your email and password</p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
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
                placeholder="••••••••"
              />
            </div>

            {error ? <p className="text-red-400 text-sm">{error}</p> : null}

            <button
              type="submit"
              disabled={!isLoaded || isSubmitting}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:shadow-[0_6px_25px_rgba(245,158,11,0.5)] rounded-xl font-semibold text-white transition-all border-none disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="text-white/40 text-sm text-center mt-5">
            Don&apos;t have an account?{' '}
            <Link to="/sign-up" className="text-amber-400 hover:text-amber-300">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignInPage;
