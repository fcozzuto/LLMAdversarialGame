def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    r = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r) or ("catcher" in r)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    parity = t & 1

    def clamp_inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obs_pen(x, y):
        if (x, y) in obs:
            return 10**9
        p = 0
        if w > 1 and h > 1:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (x + ax, y + ay) in obs:
                        p += 2
        return p

    # Build a deterministic "direct" direction and an alternating "side-step" direction.
    dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
    dy_dir = 0 if oy == sy else (1 if oy > sy else -1)

    # Side-step rotates the intended vector to avoid zigzag traps.
    # If parity==0: (dx,dy)->(dy,-dx), else: (dx,dy)->(-dy,dx)
    if parity == 0:
        dx_side, dy_side = dy_dir, -dx_dir
    else:
        dx_side, dy_side = -dy_dir, dx_dir

    main_dx, main_dy = (dx_dir, dy_dir) if (parity == 0) else (dx_side, dy_side)
    alt_dx, alt_dy = (dx_side, dy_side) if (parity == 0) else (dx_dir, dy_dir)

    want_toward = is_pursuer
    # Prefer toward for pursuer; for evader invert scoring.
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inside(nx, ny):
            continue
        v = dist2(nx, ny)
        # toward: minimize dist2, away: maximize dist2
        if want_toward:
            v = -v
        # Bias: choose moves consistent with either main or alt direction depending on turn parity.
        align_main = (dx == main_dx and dy == main_dy)
        align_alt = (dx == alt_dx and dy == alt_dy)
        v += (2 if align_main else 0) + (1 if align_alt else 0)
        # Obstacle repulsion
        v -= obs_pen(nx, ny)
        # Boundary safety (reduce staying on edges if tie)
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        v -= 0.25 if edge else 0.0

        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move