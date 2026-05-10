def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_score_for(posx, posy):
        d = cheb(posx, posy, ox, oy)
        if pursuer:
            # Strong capture bias (capture radius 0): exact match best.
            # Small mobility bonus to avoid boundary/obstacle traps.
            m = 0
            for dx, dy in dirs:
                if inb(posx + dx, posy + dy):
                    m += 1
            return (-d * 1000.0) + (m * 0.5)
        else:
            m = 0
            for dx, dy in dirs:
                if inb(posx + dx, posy + dy):
                    m += 1
            return (d * 1000.0) + (m * 0.5)

    best = None
    best_val = None
    # One-step lookahead: prefer moves that create better immediate position or reduce escape options.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Captured immediately
        if nx == ox and ny == oy:
            return [dx, dy]
        # Evaluate after our move (deterministic): small additional consideration of next step improvement.
        v0 = best_score_for(nx, ny)
        v1 = v0
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if not inb(nnx, nny):
                continue
            if pursuer:
                v1 = min(v1, best_score_for(nnx, nny))  # pessimistic helps commitment under pursuit
            else:
                v1 = max(v1, best_score_for(nnx, nny))
        # Choose maximizing for pursuer, minimizing for evader (we already signaled in scoring)
        val = v0 + (v1 * 0.05)
        if best is None or (val > best_val if pursuer else val > best_val):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]