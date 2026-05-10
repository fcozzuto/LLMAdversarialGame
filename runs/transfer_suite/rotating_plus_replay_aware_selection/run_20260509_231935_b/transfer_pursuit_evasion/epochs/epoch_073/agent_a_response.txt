def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    env = (observation.get("environment_name") or "").lower()
    i_am_pursuer = ("pursuer" in self_role and "evader" not in self_role) or ("pursuit" in env)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x, y, x2, y2):
        dx, dy = x - x2, y - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Tie-breakers: prefer progress and corner pressure for pursuer; prefer staying away from opponent for evader.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)

        # local obstacle proximity (prefer moves that don't get "stuck" near obstacles)
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    near_obs += 1

        # diagonal "progress" toward/away: compare with current relative position
        relx, rely = ox - sx, oy - sy
        nrelx, nrely = ox - nx, oy - ny
        if i_am_pursuer:
            # minimize distance; if equal, reduce obstacle proximity; if still equal, move toward opponent direction
            toward = (1 if (nx - sx) * relx >= 0 and relx != 0 else 0) + (1 if (ny - sy) * rely >= 0 and rely != 0 else 0)
            val = (-dist, -near_obs, toward, -nx, -ny)
        else:
            # maximize distance; if equal, reduce obstacle proximity; if still equal, move away direction consistently
            away = (1 if (nx - sx) * nrelx >= 0 and nrelx != 0 else 0) + (1 if (ny - sy) * nrely >= 0 and nrely != 0 else 0)
            val = (dist, -near_obs, away, nx, ny)

        if best_val is None or val > best_val if not i_am_pursuer else val > best_val:
            best_val = val
            best_move = [dx, dy]

    if legal(sx, sy):
        return best_move if best_move != [0, 0] or best_val is not None else [0, 0]
    return best_move