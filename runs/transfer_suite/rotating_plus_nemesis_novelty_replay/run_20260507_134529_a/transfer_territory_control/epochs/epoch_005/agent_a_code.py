def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def to_set(key):
        out = set()
        for p in observation.get(key, None) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    resources = to_set("resources")
    rxcount = int(observation.get("remaining_resource_count", 0) or 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    center = (w // 2, h // 2)

    def nearest_manhat(goalset):
        if not goalset:
            return 99
        best = 99
        for gx, gy in goalset:
            d = abs(gx - sx) + abs(gy - sy)
            if d < best:
                best = d
        return best

    near_self = nearest_manhat(self_terr)
    near_opp = nearest_manhat(opp_terr)
    near_un = nearest_manhat(unclaimed)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in resources:
            score += 90 + (10 if rxcount > 0 else 0)
        if (nx, ny) in opp_terr:
            score += 200  # flipping on entry is enabled

        # Prefer expanding along frontier: adjacent to our territory or opponent territory
        if self_terr:
            for tx, ty in self_terr:
                if max(abs(nx - tx), abs(ny - ty)) == 1:
                    score += 20
                    break
        if opp_terr:
            for tx, ty in opp_terr:
                if max(abs(nx - tx), abs(ny - ty)) == 1:
                    score += 14
                    break

        # Keep moving "usefully": towards center early, towards unclaimed later
        dist_center = abs(nx - center[0]) + abs(ny - center[1])
        score += -dist_center // 2

        # If we're already close to unclaimed and far from opponent, avoid useless center drift
        if near_un <= 2 and near_opp > 3:
            score += -((abs(nx - sx) + abs(ny - sy)) // 2)

        # If opponent is close, pressure it
        if near_opp <= 3:
            score += -((abs(nx - center[0]) + abs(ny - center[1])) // 3)

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], moves.index((t[1], t[2])) if (t[1], t[2]) in moves else 0))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]