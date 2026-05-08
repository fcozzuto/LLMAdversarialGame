def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8_cnt(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = 0

        if (nx, ny) in resources:
            score += 9
        if (nx, ny) in self_terr:
            score += 2
        if (nx, ny) in opp_terr:
            score += 12
            score -= 0.75 * dist_opp  # avoid being too adjacent when counterclaimed
        if (nx, ny) in unclaimed:
            frontier = neigh8_cnt(nx, ny, opp_terr)
            score += 3 + 4 * frontier  # prioritize pushing into opponent-adjacent unclaimed
            score -= 0.25 * dist_opp

        # Keep progress: prefer moving closer to strongest frontier cell in 1-step neighborhood
        if unclaimed:
            best_local = 10**9
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    tx, ty = nx + ddx, ny + ddy
                    if not inb(tx, ty):
                        continue
                    if (tx, ty) in unclaimed:
                        frontier = neigh8_cnt(tx, ty, opp_terr)
                        d = abs(tx - ox) + abs(ty - oy)
                        val = -frontier * 2 + d * 0.15  # smaller is better
                        if val < best_local:
                            best_local = val
            if best_local < 10**9:
                score += max(0, 6 - best_local)

        # Mild center/expansion bias to avoid getting stuck
        score += 0.03 * (nx + ny)

        if score > best_score:
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]