def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_adv(px, py):
        best = None
        best_key = (-10**9, 10**9)
        for rx, ry in resources:
            md = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we're closer to; tie-break by smaller own distance.
            key = (od - md, -md)
            if key > best_key or (key == best_key and (best is None or md < best_key[1])):
                best_key = key
                best = (rx, ry, md)
        return best_key  # (advantage, -my_dist)

    candidates = []
    moves = (-1, 0, 1)
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                adv, neg_md = best_adv(nx, ny)
                # Small secondary preference: move that also slightly reduces opponent's best advantage.
                opp_adv, _ = best_adv(ox, oy)
                # Deterministic scoring tuple.
                candidates.append(((adv, neg_md, -abs((nx - ox)) - abs((ny - oy))), [dx, dy]))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]