import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import api from '@/services/api';
import { setTokens } from '@/store/slices/authSlice';
import type { AppDispatch } from '@/store';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const onSubmit = async (data: FormValues) => {
    try {
      const res = await api.post('/auth/login', data);
      dispatch(setTokens(res.data));
      navigate(from, { replace: true });
    } catch (err) {
      console.error(err);
      alert('Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in-down">
          <h1 className="text-4xl font-bold text-gradient-primary mb-4">
            Music Sync Hub
          </h1>
          <p className="text-text-secondary">
            Sign in to sync your music across platforms
          </p>
        </div>

        {/* Login Form */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="glass-card p-8 space-y-6 animate-fade-in-up"
        >
          <h2 className="text-2xl font-semibold text-center mb-6">Sign In</h2>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="input-glass"
              placeholder="Enter your email"
              {...register('email')}
            />
            {errors.email && (
              <p className="text-red-400 text-sm mt-2">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input-glass"
              placeholder="Enter your password"
              {...register('password')}
            />
            {errors.password && (
              <p className="text-red-400 text-sm mt-2">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Signing in...
              </span>
            ) : (
              'Sign In'
            )}
          </button>

          <div className="text-center">
            <p className="text-text-secondary text-sm">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className="text-gradient-accent hover:underline font-medium"
              >
                Create account
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
} 