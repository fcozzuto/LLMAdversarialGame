def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(x, y) for x, y in (observation.get("obstacles") or [])}
    my_set = {(x, y) for x, y in (observation.get("self_territory") or [])}
    opp_set = {(x, y) for x, y in (observation.get("opponent_territory") or [])}
    un_set = {(x, y) for x, y in (observation.get("unclaimed_cells") or [])}
    behind = observation.get("self_territory_count", len(my_set)) < observation.get("opponent_territory_count", len(opp_set))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set: return True
        return False
    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles: c += 1
        return c

    if sx < 0 or sy < 0: return [0, 0]

    # Choose a deterministic target: attack opponent frontier when behind; else expand toward safe unclaimed.
    if behind and opp_set:
        frontier = []
        for (x, y) in opp_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        nx, ny = x + dx, y + dy
                        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in opp_set:
                            frontier.append((nx, ny))
        candidates = frontier or list(opp_set)
        tx, ty = min(candidates, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), obst_near(p[0], p[1]), p[0], p[1]))
    else:
        # Anchor to our territory if possible, otherwise to unclaimed.
        anchors = list(my_set) if my_set else [(sx, sy)]
        if un_set:
            best = None
            for (ux, uy) in un_set:
                d = min(abs(ax - ux) + abs(ay - uy) for ax, ay in anchors)
                score = (d, obst_near(ux, uy), abs(ux - (w - 1) / 2) + abs(uy - (h - 1) / 2), ux, uy)
                if best is None or score < best[0]:
                    best = (score, (ux, uy))
            tx, ty = best[1]
        else:
            # Fall back: if no unclaimed, head toward opponent if adjacent to break stalemate; else hold.
            tx, ty = (sx, sy) if not opp_set else min(opp_set, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    # Pick next move that best approaches target; add small preference for stepping onto opponent cells when attacking.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps us in place; treat as same position
        is_opp = (nx, ny) in opp_set
        val = (abs(nx - tx) + abs(ny - ty), -1 if (behind and is_opp) else 0, obst_near(nx, ny), 0 if adj_opp(nx, ny) else 1, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]