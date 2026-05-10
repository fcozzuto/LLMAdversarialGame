def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        def tgt_key(c):
            x, y = c
            # Prefer contested cells: close to opponent, not too far from us.
            return (man(x, y, ox, oy) * 2 - man(x, y, sx, sy)) + (0 if (x, y) in oppT else 3)
        target = sorted([tuple(c) for c in unclaimed], key=tgt_key)[0]
    else:
        # No unclaimed: push towards opponent side deterministically.
        target = (0, 0) if (ox + oy) < (w - 1 + h - 1) else (w - 1, h - 1)

    best = (0, 0)
    best_val = -10**18
    tx, ty = target
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in oppT:
            val += 1200
        if (nx, ny) not in selfT:
            if (nx, ny) in unclaimed:
                val += 700
            else:
                val += 50
        # Progress toward target
        curd = man(sx, sy, tx, ty)
        newd = man(nx, ny, tx, ty)
        val += (curd - newd) * 40
        # Mild pressure: move to cells that reduce distance to opponent when chasing
        val += (man(sx, sy, ox, oy) - man(nx, ny, ox, oy)) * 5
        # Prefer moving outward from our corner if possible (edge-favoring archetype)
        val += (nx - sx) * (1 if sx <= w // 2 else -1) + (ny - sy) * (1 if sy <= h // 2 else -1)
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]