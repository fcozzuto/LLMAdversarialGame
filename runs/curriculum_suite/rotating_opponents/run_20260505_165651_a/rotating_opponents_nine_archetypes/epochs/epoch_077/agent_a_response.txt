def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (value, tie, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            val = -10**9
            tie = 0
        else:
            # Prefer moving into positions that make us closer to a resource than the opponent.
            best_res = None
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                if blocked(rx, ry):
                    continue
                self_d = abs(rx - nx) + abs(ry - ny)
                opp_d = abs(rx - ox) + abs(ry - oy)
                gain = opp_d - self_d  # positive means we are closer
                # Bias toward nearer "contested" targets, and avoid just following.
                score = (gain * 100) - self_d + (opp_d - self_d)
                # Deterministic tie-break: smallest (not blocked) coordinates
                t = (-(gain), self_d, -opp_d, rx, ry)
                if best_res is None or t < best_res[0]:
                    best_res = (t, score)
            if best_res is None:
                val = -abs(w - 1 - nx) - abs(h - 1 - ny)  # fallback: drift to far side
            else:
                val = best_res[1]
            # Small obstacle proximity penalty (discourage steering too tight)
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obs:
                        adj_pen += 1
            val -= adj_pen * 2
            tie = 0
        cand = (val, tie, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[2], best[3]]