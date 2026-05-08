def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0, sx, sy))
            else:
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 50))
    close_bonus = 2.0 + (12.0 - min(12, turns)) * 0.05

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        # Immediate pickup preference
        pickup = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                pickup = 10000
                break
        if pickup:
            return [dx, dy]

        if not resources:
            # deterministic move: drift toward center
            tx, ty = (w - 1) // 2, (h - 1) // 2
            s = -(dist(nx, ny, tx, ty))
        else:
            # Choose best race target; score move by next position advantage
            local_best = 10**18
            local_best2 = 10**18
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # smaller is better: my distance minus opponent distance advantage
                race = myd - 0.95 * opd - close_bonus / (1 + myd)
                if race < local_best:
                    local_best2 = local_best
                    local_best = race
                elif race < local_best2:
                    local_best2 = race
            # small tie-break for moving closer to best target
            s = -local_best - 0.05 * local_best2
        if s > best_score:
            best_score = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]