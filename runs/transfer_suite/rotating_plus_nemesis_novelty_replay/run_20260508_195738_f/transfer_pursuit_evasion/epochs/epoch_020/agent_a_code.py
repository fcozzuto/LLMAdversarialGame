def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in self_role) or ("evader" in opp_role and "purs" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Simple one-step projection target
    vx, vy = (ox - sx), (oy - sy)
    if vx == 0 and vy == 0:
        tx, ty = ox, oy
    else:
        tx, ty = ox + (1 if vx > 0 else -1 if vx < 0 else 0), oy + (1 if vy > 0 else -1 if vy < 0 else 0)
    tx = 0 if tx < 0 else (w - 1 if tx >= w else tx)
    ty = 0 if ty < 0 else (h - 1 if ty >= h else ty)

    # Pursuer tries to reach target; Evader tries to maximize distance from pursuer (proxy) / target
    best_dxdy = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_target = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)

        if self_is_evader:
            # Prefer increasing distance to opponent and drifting away from projected target
            val = (d_opp * 4 + d_target)
        else:
            # Prefer reducing distance to opponent and approaching projected target
            val = (-d_opp * 3 - d_target)

        # Deterministic tie-break: prefer staying mobile (diagonal), then larger x step, then larger y step
        diag = 1 if dx != 0 and dy != 0 else 0
        tie = (val, diag, abs(dx), abs(dy), -nx, -ny)
        if best_val is None or tie > best_val:
            best_val = tie
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]