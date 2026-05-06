def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):  # Manhattan
        return abs(a - c) + abs(b - d)

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource-denial: pick a target where opponent is much farther than us.
        # For each target resource, compute margin = opp_dist - self_dist; maximize margin.
        best_margin = None
        best_selfd = None
        for rx, ry in resources:
            selfd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            margin = oppd - selfd
            if best_margin is None or margin > best_margin or (margin == best_margin and selfd < best_selfd):
                best_margin, best_selfd = margin, selfd

        # Small tie-breakers: prefer moves that also keep distance from opponent (reduce interception risk).
        opp_to_next = man(nx, ny, ox, oy)
        key = (-best_margin, best_selfd, -opp_to_next, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]