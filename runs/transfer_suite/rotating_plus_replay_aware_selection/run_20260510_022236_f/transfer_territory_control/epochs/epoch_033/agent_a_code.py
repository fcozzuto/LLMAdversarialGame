def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def adj_to_set(x, y, S):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    return True
        return False

    if not inb(sx, sy):
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    candidates = []
    for x, y in unclaimed:
        if inb(x, y):
            to_opp = adj_to_set(x, y, opp_terr)
            dist = abs(x - sx) + abs(y - sy)
            # Push hard toward opponent-adjacent unclaimed to expand fast
            val = (140 if to_opp else 70) - dist + (2 if (x, y) in my_terr else 0)
            candidates.append((val, x, y))
    if not candidates:
        for x, y in opp_terr:
            if inb(x, y):
                near_un = adj_to_set(x, y, unclaimed)
                dist = abs(x - sx) + abs(y - sy)
                # Attack opponent cells that border unclaimed
                val = (120 if near_un else 60) - dist + (5 if observation.get("turn_index", 0) % 10 == 0 else 0)
                candidates.append((val, x, y))
    if not candidates:
        # Fallback: nearest non-obstacle cell
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    candidates.sort(reverse=True)
    _, tx, ty = candidates[0]

    # Choose valid step that most reduces distance to target; tie-break toward attacking (entering opp terr)
    best = None
    best_key = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        enter_attack = 1 if (nx, ny) in opp_terr else 0
        # Slightly prefer moving even when distance same, to avoid stagnation
        moved = 1 if (dx != 0 or dy != 0) else 0
        key = (-(dist), -enter_attack, -moved)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]