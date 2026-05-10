def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Deterministically choose a frontier target to expand/steal.
    def adj_count(cell, S):
        cx, cy = cell
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in S:
                c += 1
        return c

    candidates = []
    for uc in unclaimed:
        if adj_count(uc, oppT) > 0:
            candidates.append(uc)

    if candidates:
        target = max(candidates, key=lambda p: (adj_count(p, oppT), -p[1], -p[0]))
    else:
        candidates2 = [uc for uc in unclaimed if adj_count(uc, selfT) > 0]
        if candidates2:
            target = max(candidates2, key=lambda p: (adj_count(p, selfT), -p[1], -p[0]))
        else:
            target = (w // 2, h // 2)

    tx, ty = target

    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in oppT:
            # Steal pressure: entering opponent territory flips.
            score += 10
            # Prefer moves that immediately border more unclaimed space.
            un_adj = 0
            for ddx, ddy in dirs:
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in unclaimed:
                    un_adj += 1
            score += 2 * un_adj
        elif (nx, ny) in selfT:
            score += 3
        elif (nx, ny) in unclaimed:
            score += 6

        # Move toward chosen target with small preference for improving adjacency.
        score += -md(nx, ny, tx, ty)

        # Small tie-breaker: bias toward upper-left only via deterministic ordering.
        score += 0.000001 * (-(ny * w + nx))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]