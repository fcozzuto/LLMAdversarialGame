def choose_move(observation):
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_val(x, y):
        if (x, y) in obstacles:
            return -10**9
        val = 0
        if (x, y) in self_set:
            val += 2
        elif (x, y) in opp_set:
            val += 13  # beneficial counter-claim on entry (flip enabled)
        elif (x, y) in unclaimed:
            val += 7  # claim neutral ground
        else:
            val += 3  # safe-ish unknown/unlisted
        dcenter = abs(x - cx) + abs(y - cy)
        dopp = abs(x - ox) + abs(y - oy)
        val += (-dcenter) * 0.9 + (dopp) * 0.6
        # Prefer cells where we are not slower than opponent to occupy
        dself = abs(x - sx) + abs(y - sy)
        dopp = abs(x - ox) + abs(y - oy)
        val += (dopp - dself) * 4.2
        # Local "openness": fewer obstacles around target is better
        block = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                block += 1
        val += (8 - block) * 0.5
        return val

    best = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate immediate and one-step "commit" in same direction
        v1 = neigh_val(nx, ny)
        nnx, nny = nx + dx, ny + dy
        v2 = neigh_val(nnx, nny) if inb(nnx, nny) and (nnx, nny) not in obstacles else -10**6
        # If moving into opponent territory, slightly prefer doing so only when it also pulls away from center less
        stick = (1.5 if (nx, ny) in opp_set else 0) - (0.4 * (abs(nx - cx) + abs(ny - cy)))
        score = v1 * 1.0 + v2 * 0.45 + stick
        if score > best[2]:
            best = (dx, dy, score)

    if best[2] < -10**8:
        return [0, 0]
    return [best[0], best[1]]