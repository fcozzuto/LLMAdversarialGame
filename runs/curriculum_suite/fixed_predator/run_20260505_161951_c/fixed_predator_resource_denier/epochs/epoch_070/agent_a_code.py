def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def clamp_move(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return [dx, dy]
    if not resources:
        best = [0, 0]; bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_goal = abs(nx - tx) + abs(ny - ty)
            v = d_opp * 400 - d_goal * 3
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Approximate opponent's next progress: they can reduce their chebyshev distance by 1 if not blocked.
    # Evaluate how our move changes "capture advantage" (self closer than opp) and "denial strength".
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        worst_penalty = 0
        best_gain = -10**18
        for rx, ry in resources:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            d_o_next = d_o - 1 if d_o > 0 else 0
            advantage = d_o_next - d_s  # positive means we are closer even after their next step
            # Deny if they currently are closer: push advantage upward; if we can't take, still reduce their lead.
            take_term = 10 * advantage
            deny_term = -3 * max(0, d_o - d_s)  # punish letting ourselves fall behind
            center_term = -0.05 * (abs(nx - (w/2)) + abs(ny - (h/2)))
            v = take_term + deny_term + center_term
            if advantage >= 0:
                if v > best_gain: best_gain = v
            else:
                worst_penalty += (-advantage) * (-advantage) * 0.1
        # If we can secure at least one resource (best_gain), prioritize that; otherwise avoid making things worse.
        v_move = best_gain - worst_penalty
        # Secondary tie-break: prefer moves that increase distance from opponent for safety if unclear.
        v_move += 0.01 * cheb(nx, ny, ox, oy)
        if v_move > bestv:
            bestv = v_move; best = [dx, dy]
    return best