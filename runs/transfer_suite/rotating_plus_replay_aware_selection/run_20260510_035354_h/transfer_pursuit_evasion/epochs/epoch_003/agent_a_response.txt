def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer_like = ("purs" in self_role) or (self_role == "pursuer") or ("evad" in opp_role and "purs" in self_role) or ("evad" in self_role and "purs" in opp_role)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    def obstacle_prox(x, y):
        best = 99
        for ax, ay in obstacles:
            d = abs(x-ax) + abs(y-ay)
            if d < best:
                best = d
        return best  # smaller => worse

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_dxdy = (0, 0)
    if pursuer_like:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            center = dist2(nx, ny, cx, cy)
            # Prefer approaching while not walking into obstacle-adjacent traps; also bias moving to cut off corners.
            prox = obstacle_prox(nx, ny)
            corner_bias = -(min(abs(nx-fx)+abs(ny-fy) for fx,fy in corners))
            val = (d, center, -prox, corner_bias, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_dxdy = (dx, dy)
    else:
        # evader
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_after = dist2(nx, ny, ox, oy)
            # stay closer to far corner (but only if it doesn't reduce distance too much)
            toward = -dist2(nx, ny, far_corner[0], far_corner[1])
            center = dist2(nx, ny, cx, cy)
            # penalize getting too close to obstacles
            prox = obstacle_prox(nx, ny)
            # discourage edges only when equally good, to survive longer and avoid corner-locking by zigzags
            edge = min(nx, w-1-nx) + min(ny, h-1-ny)
            val = (-d_after, edge, -prox, -toward, center, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_dxdy = (dx, dy)
    return [int(best_dxdy[0]), int(best_dxdy[1])]