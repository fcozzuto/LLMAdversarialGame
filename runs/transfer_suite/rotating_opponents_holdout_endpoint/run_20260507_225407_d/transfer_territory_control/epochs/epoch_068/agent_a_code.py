def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    # Candidate move destinations (8-neighborhood + stay)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Heuristic target: prioritize unclaimed adjacent to opponent territory; else nearest unclaimed; else nearest opponent territory.
    targets = []
    for (ox, oy) in opp_t:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    targets.append((nx, ny))
    if not targets and unclaimed:
        targets = list(unclaimed)
    if not targets and opp_t:
        targets = list(opp_t)
    if not targets:
        return [0, 0]

    # Score move: prefer landing on unclaimed/opp, and generally reduce distance to best target.
    def manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best_target = None
    # Deterministic pick: minimal (distance, x, y) with tie.
    best_key = None
    for t in targets:
        key = (manh((sx, sy), t), t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = t

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = -manh((nx, ny), (tx, ty))
        if (nx, ny) in unclaimed:
            val += 2000
        if (nx, ny) in opp_t:
            val += 900
        # Avoid moving away from the chosen direction when both axes matter.
        if dx != 0 and ((tx - sx) * dx <= 0):
            val -= 8
        if dy != 0 and ((ty - sy) * dy <= 0):
            val -= 8
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]