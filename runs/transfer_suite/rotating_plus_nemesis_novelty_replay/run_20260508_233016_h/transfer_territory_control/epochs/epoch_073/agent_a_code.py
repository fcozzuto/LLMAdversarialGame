def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    nbrs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in selfT:
            score += 2
        elif (nx, ny) in oppT:
            score += 9 - 0.3 * man(nx, ny, sx, sy)
        elif (nx, ny) in unclaimed:
            score += 7

        # Frontier bonus: move toward/along unclaimed boundary
        neigh_uncl = 0
        for ddx, ddy in nbrs8:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in unclaimed:
                neigh_uncl += 1
        score += 1.2 * neigh_uncl

        # Tactical pressure: prefer positions closer to opponent than to ourselves
        d_opp = man(nx, ny, ox, oy)
        d_self = man(nx, ny, sx, sy)
        score += (4.0 - 0.35 * d_opp) + 0.05 * (-d_self)

        # If opponent is very close, prioritize claiming their territory/unclaimed adjacent
        d_now = man(sx, sy, ox, oy)
        if d_now <= 4:
            if (nx, ny) in oppT:
                score += 6
            if (nx, ny) in unclaimed:
                score += 3

        # Tie-break deterministically toward larger dx,dy (stable order via tuple)
        key = (score, dx, dy, nx, ny)
        if key > (best_score, 0, 0, -1, -1):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best