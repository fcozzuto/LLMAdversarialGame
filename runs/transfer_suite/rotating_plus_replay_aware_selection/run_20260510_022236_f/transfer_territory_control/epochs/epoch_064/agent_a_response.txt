def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_unclaimed_dist(x, y):
        if not unclaimed:
            return 0
        best = 10**9
        # small cap for determinism/efficiency
        cap = 48 if len(unclaimed) > 48 else len(unclaimed)
        for i in range(cap):
            cx, cy = unclaimed[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best if best != 10**9 else 0

    # Defensive: avoid getting stuck against obstacles; prefer moves that expand territory
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**15
        else:
            score = 0
            if (nx, ny) in unclaimed:
                score += 120
            if (nx, ny) in self_terr:
                score += 10
            if (nx, ny) in op_terr:
                score += 35  # flipping on entry
            # Push toward nearest unclaimed; also keep distance from obstacles indirectly
            d_un = nearest_unclaimed_dist(nx, ny)
            score += max(0, 30 - 3 * d_un)
            # Prefer progressing away from current corner-ish if unclaimed exists (deterministic tie-break)
            score += - (nx + ny) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: smaller dx, then smaller dy magnitude
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]