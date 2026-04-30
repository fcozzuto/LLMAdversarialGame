def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_resource_score(x, y):
        if not resources:
            return None
        bestd = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < bestd:
                bestd = d
        return bestd

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        rd = best_resource_score(nx, ny)
        if rd is not None:
            # Prefer reducing distance to nearest resource; tie-break by staying away from opponent.
            od = abs(ox - nx) + abs(oy - ny)
            key = (-rd, -od, dx, dy)
        else:
            # No resources known: move away from opponent.
            od = abs(ox - nx) + abs(oy - ny)
            key = (od, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best

    # If all neighbor moves are blocked, stay in place if possible; otherwise move to the first valid adjacent cell.
    if 0 <= sx < w and 0 <= sy < h and (sx, sy) not in obstacles:
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]