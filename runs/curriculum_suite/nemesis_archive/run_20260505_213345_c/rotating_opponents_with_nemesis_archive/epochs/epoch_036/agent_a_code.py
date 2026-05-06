def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        cx, cy = sx, sy
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if not valid(nx, ny):
                continue
            mind = None
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if mind is None or d < mind:
                    mind = d
            dopp = abs(ox - nx) + abs(oy - ny)
            val = (mind, -dopp)  # prioritize closer resource; tie-break run slightly away from opponent
            if best is None or val < best[0]:
                best = (val, dx, dy)
        if best is not None:
            return [best[1], best[2]]

    # Fallback: move toward opponent if no resources, else stay/avoid obstacles
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand.append((abs(ox - nx) + abs(oy - ny), dx, dy))
    if cand:
        cand.sort(key=lambda t: (t[0], t[1], t[2]))
        return [cand[0][1], cand[0][2]]

    return [0, 0]