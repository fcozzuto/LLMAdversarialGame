def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Build deterministic target set: prefer unclaimed, then frontier cells near opponent territory.
    targets = []
    for (x, y) in unclaimed:
        if inb(x, y):
            bonus = 0 if (x, y) in oppT else 5
            targets.append(((man(x, y, sx, sy) * 2 + man(x, y, ox, oy)) - bonus, x, y))
    # Frontier-ish: cells adjacent to opponent territory (unclaimed or ours) to enable pressure/transfer.
    adj_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    if not targets:
        seen = set()
        for (x, y) in oppT:
            for dx, dy in adj_dirs:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) in seen:
                    continue
                seen.add((nx, ny))
                if (nx, ny) not in oppT:
                    # Prefer empty/unclaimed or pushing further in our direction.
                    prior = -20 if (nx, ny) in unclaimed else (-5 if (nx, ny) in selfT else 0)
                    targets.append((man(nx, ny, sx, sy) - prior, nx, ny))

    if targets:
        targets.sort(key=lambda t: (t[0], t[1], t[2]))
        tx, ty = targets[0][1], targets[0][2]
    else:
        # No useful cells: head toward opponent or center deterministically.
        tx, ty = (w // 2, h // 2) if (sx + sy) <= (ox + oy) else (ox, oy)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move, best_val = (0, 0), -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that go closer to target and create immediate capture opportunities.
        close = -man(nx, ny, tx, ty)
        immediate = 0
        if (nx, ny) in oppT:
            immediate += 45  # entering opponent territory flips control
        elif (nx, ny) in selfT:
            immediate += 5
        else:
            # Unclaimed: claim it; slightly prefer edge cells to reduce counterplay symmetry.
            immediate += 18 if (nx, ny) in unclaimed else 8
            if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
                immediate += 5
        # Also gently reduce distance to opponent to counterclaim sooner.
        engage = -man(nx, ny, ox, oy) // 2
        val = immediate + close + engage
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        # If blocked everywhere, stay.
        return [0, 0]
    return [int(dx), int(dy)]