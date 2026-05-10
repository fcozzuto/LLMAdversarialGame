def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [tuple(c) for c in unclaimed]

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    man = lambda ax, ay, bx, by: abs(ax - bx) + abs(ay - by)

    def adjacent_to_self(cell):
        x, y = cell
        for dx, dy in neigh8:
            if (x + dx, y + dy) in selfT:
                return True
        return False

    frontier = [c for c in unclaimed if adjacent_to_self(c)]
    pool = frontier if frontier else unclaimed

    # Pick a small deterministic set of targets (edge-favoring vs opponent)
    if not pool:
        target = (w // 2, h // 2)
        dx = 0 if sx == target[0] else (1 if sx < target[0] else -1)
        dy = 0 if sy == target[1] else (1 if sy < target[1] else -1)
        return [dx, dy]

    def tgt_key(c):
        x, y = c
        edge = (x == 0 or y == 0 or x == w - 1 or y == h - 1)
        return (man(x, y, sx, sy) * 2 + man(x, y, ox, oy) + (0 if edge else 6) + (0 if c in oppT else 0))

    targets = sorted(pool, key=tgt_key)[:18]
    ordered_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in ordered_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**17
        else:
            # Prefer reaching near our frontier targets quickly
            dmin = 10**9
            for tx, ty in targets:
                dmin = min(dmin, man(nx, ny, tx, ty))
            # Encourage attacking opponent territory (flip on entry)
            atk = 0
            if (nx, ny) in oppT:
                atk = 250
            # Slightly prefer moving toward opponent to pressure edge claimer
            toward_opp = -man(nx, ny, ox, oy) * 2
            # Mild preference for expanding unclaimed vicinity
            on_unclaimed = 60 if (nx, ny) in set(unclaimed) else 0
            # Also prefer staying on/near our territory to avoid losing control
            on_self = 15 if (nx, ny) in selfT else 0
            val = atk + toward_opp + on_unclaimed + on_self - dmin * 6
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]