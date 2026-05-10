def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    sx, sy = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obs_set = set((int(a), int(b)) for a, b in obstacles if 0 <= int(a) < w and 0 <= int(b) < h)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) and ("evad" not in self_role)
    if not i_am_pursuer and ("purs" in opp_role) and ("evad" not in opp_role):
        i_am_pursuer = False
    if not ("purs" in self_role or "evad" in self_role):
        i_am_pursuer = True  # fallback

    moves = [[dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-break order: prioritize smaller dx then smaller dy
    moves.sort(key=lambda m: (m[0], m[1]))

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Try to avoid obstacles; if move lands on obstacle, it'll be rejected anyway.
    best_move = [0, 0]
    if i_am_pursuer:
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
                continue
            d2 = dist2(nx, ny, ox, oy)
            # Higher is better: closer to evader, and reduce chance of being cornered by obstacles
            val = -d2
            # Bonus for moves that decrease distance compared to current
            cur = dist2(sx, sy, ox, oy)
            if d2 < cur:
                val += 0.5
            # Small penalty for moving into positions with more obstacle neighbors (to reduce trapping)
            neigh = 0
            for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1)):
                tx, ty = nx + ddx, ny + ddy
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs_set:
                    neigh += 1
            val -= 0.05 * neigh
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = -10**18
        cur_d2 = dist2(sx, sy, ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
                continue
            d2 = dist2(nx, ny, ox, oy)
            # Higher is better: increase distance; also prefer moving toward board edges deterministically
            edge = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val = d2
            if d2 > cur_d2:
                val += 0.5
            val += -0.02 * edge
            # Penalize getting closer in one-step without escape
            val -= 0.03 * (cur_d2 - d2) if d2 < cur_d2 else 0
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]