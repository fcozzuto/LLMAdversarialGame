def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    # Focus: step toward nearest opponent territory (counterclaim pressure); if none, expand into unclaimed.
    if opp_t:
        target = min(opp_t, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        target = min(unclaimed if unclaimed else self_t, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1])) if (unclaimed or self_t) else (sx, sy)

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        # Immediate capture value (flipping on entry is enabled).
        if (nx, ny) in opp_t:
            v += 160
        elif (nx, ny) in unclaimed:
            v += 55
        elif (nx, ny) in self_t:
            v += 8
        else:
            v += 2

        # Move toward target.
        dcur = abs(target[0] - sx) + abs(target[1] - sy)
        dnew = abs(target[0] - nx) + abs(target[1] - ny)
        v += (dcur - dnew) * 6

        # Avoid stepping into opponent-adjacent "pressure" while not giving up capture.
        near_opp = 1 if any(adj8((nx, ny), o) for o in opp_t) else 0
        near_self = 1 if any(adj8((nx, ny), s) for s in self_t) else 0
        if (nx, ny) not in opp_t:
            v -= 12 * near_opp
            v += 4 * near_self

        # Prefer moves that touch unclaimed frontier to keep expansion going.
        touch_unclaimed = 1 if any(adj8((nx, ny), u) for u in unclaimed) else 0
        v += 10 * touch_unclaimed

        # Deterministic tie-break: lowest (dx,dy) order bias via tuple comparison.
        key = (v, -abs(dx), -abs(dy), -nx, -ny)
        if best is None or key > bestv:
            bestv = key
            best = [dx, dy]

    return best if best is not None else [0, 0]