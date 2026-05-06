def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_score = None
    # Heuristic: maximize relative advantage at contested resources, then proximity.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if not resources:
            # Fallback: move toward center while staying valid
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score = -((nx - cx) ** 2 + (ny - cy) ** 2) + 0.1 * (man(nx, ny, ox, oy))
        else:
            my_best = 10**9
            opp_best = 0
            # Consider each resource as potential focus; pick the resource with best contest outcome.
            for rx, ry in resources:
                my_steps = man(nx, ny, rx, ry)
                opp_steps = man(ox, oy, rx, ry)
                # Prefer making opponent farther than self, then being close ourselves.
                rel = opp_steps - my_steps
                my_best = min(my_best, my_steps)
                opp_best = max(opp_best, opp_steps)
                score_r = rel * 10 - my_steps
                if score_r > (best_score if best_score is not None else -10**18):
                    pass
            # Compute score from the best contested resource at this neighbor
            best_r_score = -10**18
            for rx, ry in resources:
                my_steps = man(nx, ny, rx, ry)
                opp_steps = man(ox, oy, rx, ry)
                rel = opp_steps - my_steps
                r_score = rel * 10 - my_steps
                if r_score > best_r_score:
                    best_r_score = r_score
            # Small deterministic bias to progress and reduce oscillation near opponent.
            score = best_r_score + 0.01 * (opp_best - my_best) - 0.001 * man(nx, ny, ox, oy)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]