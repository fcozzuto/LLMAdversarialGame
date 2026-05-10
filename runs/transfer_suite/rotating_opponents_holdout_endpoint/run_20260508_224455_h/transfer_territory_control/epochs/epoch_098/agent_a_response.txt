def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-9:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = (0, 0, -10**9)  # dx,dy,score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer claiming toward center, while breaking opponent territory.
        dcen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 140.0
        elif (nx, ny) in unclaimed:
            val += 55.0
        elif (nx, ny) in self_terr:
            val += 18.0
        else:
            val += 8.0

        val += (22.0 - dcen)  # closer to center is better

        # Avoid oscillation / loops.
        if (nx, ny) in recent:
            val -= 45.0

        # Prefer steps that reduce distance-to-center compared to staying.
        stay_d = ((sx - cx) * (sx - cx) + (sy - cy) * (sy - cy)) ** 0.5
        if dcen < stay_d:
            val += 10.0

        # Deterministic tie-break: lexicographic preference via fixed move order.
        if val > best[2]:
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]