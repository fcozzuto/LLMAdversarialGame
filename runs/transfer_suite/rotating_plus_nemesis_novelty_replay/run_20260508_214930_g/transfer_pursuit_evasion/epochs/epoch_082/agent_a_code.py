def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_evader = False

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx*dx + dy*dy
        if is_pursuer:
            # prefer moves that reduce distance most; slight tie-break toward center
            center = (w//2, h//2)
            cd = (nx-center[0])**2 + (ny-center[1])**2
            return (-d2, cd)
        else:
            # prefer moves that increase distance most; bias toward farthest corner
            corner = max(corners, key=lambda c: (c[0]-ox)*(c[0]-ox) + (c[1]-oy)*(c[1]-oy))
            fd = (nx-corner[0])*(nx-corner[0]) + (ny-corner[1])*(ny-corner[1])
            # also avoid getting stuck near obstacles by preferring fewer adjacent obstacle cells
            adj_obs = 0
            for ax, ay in deltas:
                tx, ty = nx+ax, ny+ay
                if (tx, ty) in obs:
                    adj_obs += 1
            return (d2, fd, -adj_obs)

    best = None
    best_mv = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None:
            best, best_mv = sc, [dx, dy]
        else:
            if is_pursuer:
                # sc is tuple where first element is primary (negative d2)
                if sc < best:
                    best, best_mv = sc, [dx, dy]
            else:
                if sc > best:
                    best, best_mv = sc, [dx, dy]

    if best is None:
        # fallback: greedy straight-line with obstacle-agnostic direction, still deterministic
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            return [dx, dy]
        return [0, 0]
    return best_mv