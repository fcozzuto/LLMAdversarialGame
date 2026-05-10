def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = [0, 0]
    best_val = -10**9

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            landed = 1 if (nx, ny) in set(resources) else 0
            self_best = -10**9
            for rx, ry in resources:
                sd = cd(nx, ny, rx, ry)
                od = cd(ox, oy, rx, ry)
                # Prefer resources where we are closer; still allow blocks but reduce it.
                win = (od - sd)
                # Small bias to keep moving toward closer resources, even if not winning yet.
                val = (win * 10) - sd
                if val > self_best:
                    self_best = val

            # Landing dominates; otherwise pick the move with highest potential.
            val2 = self_best + (200 if landed else 0)

            if val2 > best_val:
                best_val = val2
                best = [dx, dy]
            elif val2 == best_val:
                # Deterministic tie-break: prefer non-staying, then lexicographic.
                if best == [0, 0] and [dx, dy] != [0, 0]:
                    best = [dx, dy]
                elif [dx, dy] != best and [dx, dy] < best:
                    best = [dx, dy]

    return best