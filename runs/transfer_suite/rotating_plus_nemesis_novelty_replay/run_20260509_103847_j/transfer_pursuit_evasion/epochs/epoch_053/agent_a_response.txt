def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_purs = any(k in sr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    opp_purs = any(k in pr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    pursuer = self_purs and not (opp_purs and not self_purs)
    if not self_purs and opp_purs:
        pursuer = False

    def sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    # Predict opponent next cell assuming it tries to increase distance from us.
    vx = sign(ox - sx)
    vy = sign(oy - sy)
    px, py = ox + vx, oy + vy
    if not inside(px, py):
        px, py = ox, oy  # fallback if blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = None

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Penalties for getting stuck near obstacles/edges (deterministic, cheap).
        adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if not inside(ax, ay):
                    adj += 1

        if pursuer:
            val = dist2(nx, ny, px, py) * 10 + dist2(nx, ny, ox, oy) + adj * 0.5
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        else:
            # Evader: maximize distance from predicted pursuer position (use our own predicted escape).
            # Here approximate by maximizing distance from our position's mirror-away point: pursuer is assumed to chase.
            chase_target_x, chase_target_y = sx + sign(sx - ox), sy + sign(sy - oy)
            if not inside(chase_target_x, chase_target_y):
                chase_target_x, chase_target_y = ox, oy
            val = dist2(nx, ny, chase_target_x, chase_target_y) * 10 - dist2(nx, ny, ox, oy) - adj * 0.5
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]