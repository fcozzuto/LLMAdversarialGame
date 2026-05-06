def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None  # (score, dx, dy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer resources where we become relatively closer than opponent (steal lanes),
            # otherwise take a less-contested resource (push to far/away side).
            best_res_score = -10**9
            for rx, ry in resources:
                dself = md(nx, ny, rx, ry)
                dopp = md(ox, oy, rx, ry)
                # If we are closer than opponent, strongly prefer; if not, prefer smaller deficit.
                rel = (dopp - dself)  # positive means we are closer
                # Mild bias toward resources that are also nearer to us (ties/early turns).
                score = rel * 10 - dself
                if score > best_res_score:
                    best_res_score = score
            # Also discourage getting too close to opponent to reduce swap contest.
            contest_penalty = md(nx, ny, ox, oy)
            total = best_res_score - 0.05 * contest_penalty
            if best is None or total > best[0]:
                best = (total, dx, dy)
        return [int(best[1]), int(best[2])]

    # No visible resources: move toward the safer far-side from opponent while avoiding obstacles.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Move to maximize distance from opponent.
        total = md(nx, ny, ox, oy)
        if best is None or total > best[0]:
            best = (total, dx, dy)
    return [int(best[1]), int(best[2])]