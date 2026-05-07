def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def king_dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate next positions (allow stay), avoid obstacles when possible.
    steps = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    # Strategic change: greedily move to the resource where we most likely arrive first,
    # with tie-break pushing us away from giving the opponent a nearer claim.
    best = None
    for nx, ny, dx, dy in candidates:
        best_cell = None
        for rx, ry in resources:
            my = king_dist(nx, ny, rx, ry)
            op = king_dist(ox, oy, rx, ry)
            # Higher is better: prefer (my-op negative) and shorter my distance.
            # Also slightly prefer resources closer to the center to reduce "edge traps".
            center = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
            val = (op - my) * 1000 - my * 10 - center * 0.1
            if best_cell is None or val > best_cell[0] or (val == best_cell[0] and my < best_cell[1]):
                best_cell = (val, my)
        if best is None or best_cell[0] > best[0] or (best_cell[0] == best[0] and best_cell[1] < best[1]):
            best = (best_cell[0], best_cell[1], dx, dy)

    return [int(best[2]), int(best[3])]