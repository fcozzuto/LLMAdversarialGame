def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corners = [c for c in corners if c not in obstacles] or corners

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    self_pt = (x, y)
    opp_pt = (ox, oy)

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        nxt = (nx, ny)
        d = cheb(nxt, opp_pt)

        # Anticipate opponent evasion: favor turning away from their position when close.
        # pursuer: lower distance strongly; also prefer staying on "safer corridors" (away from obstacles).
        # evader: raise distance strongly; also prefer reducing potential trap by not moving into corners too early.
        score = 0.0
        if role == "pursuer":
            score += -10.0 * d
            # If adjacent, prioritize immediate capture path (still deterministic).
            score += (1.0 if d == 0 else 0.0)
            # Obstacle proximity penalty (more free space is better)
            neigh_free = 0
            for ex, ey in moves:
                tx, ty = nx + ex, ny + ey
                if in_bounds(tx, ty):
                    neigh_free += 1
            score += 0.2 * neigh_free
            # Keep heading toward the corner farthest from opponent to reduce escape routes
            far_corner = max(corners, key=lambda c: cheb(c, opp_pt))
            score += -0.05 * cheb(nxt, far_corner)
        else:
            score += 10.0 * d
            # Evade: if very close, strongly prefer increasing distance and a "side-step" (avoid moving straight into them).
            if d <= 1:
                score += 1.0 * (abs(nx - ox) + abs(ny - oy))
            # Free-space preference
            neigh_free = 0
            for ex, ey in moves:
                tx, ty = nx + ex, ny + ey
                if in_bounds(tx, ty):
                    neigh_free += 1
            score += 0.15 * neigh_free
            # Flee to farthest corner from pursuer
            far_corner = max(corners, key=lambda c: cheb(c, opp_pt))
            score += -0.05 * cheb(nxt, far_corner)

        if best is None or score > best_val:
            best = [dx, dy]
            best_val = score

    if best is None:
        return [0, 0]
    return best