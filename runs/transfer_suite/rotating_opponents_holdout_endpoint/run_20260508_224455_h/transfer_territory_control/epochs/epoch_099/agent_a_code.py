def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-10:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def neighbor_count_set(x, y, s):
        c = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in s:
                c += 1
        return c

    best_dxdy = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in recent and (dx, dy) != (0, 0):
            base_pen = 22
        else:
            base_pen = 0

        dist_center = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5
        val = -dist_center * 3.0 - base_pen

        if (nx, ny) in opp_terr:
            val += 240.0 + neighbor_count_set(nx, ny, opp_terr) * 8.0
        elif (nx, ny) in unclaimed:
            val += 95.0 + neighbor_count_set(nx, ny, opp_terr) * 16.0 + neighbor_count_set(nx, ny, self_terr) * 2.0
        elif (nx, ny) in self_terr:
            val += 10.0 + neighbor_count_set(nx, ny, opp_terr) * 6.0
        else:
            val += 5.0

        # Prefer moving toward cells adjacent to opponent territory
        val += neighbor_count_set(nx, ny, opp_terr) * 12.0

        if val > best_val or (val == best_val and (dx, dy) < best_dxdy):
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]