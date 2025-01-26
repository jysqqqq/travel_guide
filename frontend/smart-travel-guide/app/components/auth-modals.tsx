'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useAuth } from '@/contexts/AuthContext'
import { toast } from 'sonner'

export function AuthModals() {
  const [isOpen, setIsOpen] = useState(false)
  const { login, register } = useAuth()
  const [isLoading, setIsLoading] = useState(false)

  // 登录表单状态
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  })

  // 注册表单状态
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  // 处理登录表单提交
  const handleLoginSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsLoading(true)
    try {
      await login(loginForm.username, loginForm.password)
      toast.success('登录成功',{position: "top-center"})
      setIsOpen(false)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '登录失败',{position: "top-center"})
    } finally {
      setIsLoading(false)
    }
  }

  // 处理注册表单提交
  const handleRegisterSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    
    if (registerForm.password !== registerForm.confirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }

    setIsLoading(true)
    try {
      await register(registerForm.username, registerForm.password, registerForm.email)
      toast.success('注册成功')
      setIsOpen(false)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '注册失败')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" className="text-gray-800 hover:text-gray-600">登录 / 注册</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] bg-white">
        <DialogHeader>
          <DialogTitle>账户</DialogTitle>
          <DialogDescription>
            登录或创建新账户以访问更多功能。
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">登录</TabsTrigger>
            <TabsTrigger value="register">注册</TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <form onSubmit={handleLoginSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="username-login">用户名</Label>
                  <Input 
                    id="username-login" 
                    value={loginForm.username}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, username: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="password-login">密码</Label>
                  <Input 
                    id="password-login" 
                    type="password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
              </div>
              <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white" disabled={isLoading}>
                {isLoading ? '登录中...' : '登录'}
              </Button>
            </form>
          </TabsContent>
          <TabsContent value="register">
            <form onSubmit={handleRegisterSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="username-register">用户名</Label>
                  <Input 
                    id="username-register" 
                    value={registerForm.username}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, username: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email-register">邮箱</Label>
                  <Input 
                    id="email-register" 
                    type="email"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, email: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="password-register">密码</Label>
                  <Input 
                    id="password-register" 
                    type="password"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, password: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="confirm-password">确认密码</Label>
                  <Input 
                    id="confirm-password" 
                    type="password"
                    value={registerForm.confirmPassword}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    required 
                    disabled={isLoading}
                  />
                </div>
              </div>
              <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white" disabled={isLoading}>
                {isLoading ? '注册中...' : '注册'}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}

