def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if not unclaimed:
        return [0, 0]

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    our_count = int(observation.get("self_territory_count", 0) or 0)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    we_are_ahead = our_count >= opp_count

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    targets = unclaimed

    # Limit candidates for speed/determinism
    if len(targets) > 35:
        targets = sorted(targets, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))[:35]

    def adj_to_our(px, py):
        for dx, dy in dirs8:
            nx, ny = px + dx, py + dy
            if (nx, ny) in self_terr:
                return True
        return False

    best = None
    best_score = 10**18
    for tx, ty in targets:
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        edge = 1 if (tx == 0 or ty == 0 or tx == w - 1 or ty == h - 1) else 0
        expand = 1 if self_terr and adj_to_our(tx, ty) else 0
        # If behind, be more aggressive toward opponent; if ahead, consolidate expansions.
        aggress = -1 if we_are_ahead else 1
        score = d_self - (0.6 * d_opp * aggress) - (2.0 * expand) + (0.15 * edge)
        # Tiny deterministic tie-break
        score = (score, tx, ty)
        if score < best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best if best is not None else unclaimed[0]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis-only fallback deterministically
        if dx != 0 and (sx + dx, sy) not in obstacles and inb(sx + dx, sy):
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles and inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]
    return [dx, dy]