def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    # Precompute nearest resource distance from current position for deterministic fallback
    if resources:
        best_r0 = min((abs(sx - x) + abs(sy - y) for x, y in resources))
    else:
        best_r0 = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_dist = abs(nx - ox) + abs(ny - oy)

        if resources:
            rdist = min(abs(nx - x) + abs(ny - y) for x, y in resources)
            # Primary: closer to resources; Secondary: farther from opponent; Tertiary: smaller move bias
            val = (-rdist, opp_dist, -(abs(dx) + abs(dy)))
        else:
            # No resources: prefer moving away from opponent a bit, else stay
            val = (opp_dist, -(abs(dx) + abs(dy)), 0)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    # If all moves blocked, try staying
    if inb(sx, sy) and (sx, sy) not in obstacles:
        return [0, 0]

    # Otherwise, pick any in-bounds, non-obstacle neighbor deterministically
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    return [0, 0]