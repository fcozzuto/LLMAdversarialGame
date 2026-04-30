def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set()
    for p in (observation.get("obstacles") or []):
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass
    resources = []
    for p in (observation.get("resources") or []):
        try:
            resources.append((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    if resources:
        tx, ty = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (w // 2, h // 2)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_res = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer getting resources; break ties by staying away from opponent and avoiding obstacles adjacency
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj += 1
        score = -d_res + 0.02 * d_opp - 0.15 * adj
        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            # deterministic tie-break: prefer higher d_opp, then fewer adjacency, then lexicographic dx,dy
            best_dopp = cheb(sx + best[1], sy + best[2], ox, oy)
            if d_opp > best_dopp:
                best = (score, dx, dy)
            elif d_opp == best_dopp:
                best_adj = 0
                bx, by = sx + best[1], sy + best[2]
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        if (bx + ax, by + ay) in obs:
                            best_adj += 1
                if adj < best_adj or (adj == best_adj and (dx, dy) < (best[1], best[2])):
                    best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]