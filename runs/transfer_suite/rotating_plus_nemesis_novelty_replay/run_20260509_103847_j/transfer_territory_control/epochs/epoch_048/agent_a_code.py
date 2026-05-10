def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if not unclaimed:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_to_self(cell):
        x, y = cell
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in selfT:
                return True
        return False

    # Prefer unclaimed frontier adjacent to our territory; otherwise, go for any unclaimed.
    frontier = [c for c in unclaimed if adj_to_self(c)]
    targets = frontier if frontier else unclaimed

    opx, opy = observation.get("opponent_position", [w - 1, h - 1])
    opx, opy = int(opx), int(opy)

    # Score targets: close to us, far from opponent; slightly prefer central expansion.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestv = None
    for tx, ty in targets:
        d_us = max(abs(tx - sx), abs(ty - sy))
        d_op = abs(tx - opx) + abs(ty - opy)
        center_bias = -(abs(tx - cx) + abs(ty - cy))
        # Avoid walking onto opponent territory explicitly (though unclaimed list shouldn't include it).
        v = (d_us * 3) - (d_op * 2) + center_bias
        if bestv is None or v < bestv:
            bestv = v
            best = (tx, ty)

    tx, ty = best
    # Move one step toward target while avoiding obstacles and preferring not to enter opponent territory.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = max(abs(tx - nx), abs(ty - ny))
        enter_op = 1 if (nx, ny) in opT else 0
        # Small tie-break: keep spreading (prefer increasing adjacency to self).
        adj = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in selfT:
                adj += 1
        score = dist + enter_op * 50 - adj * 0.01
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move