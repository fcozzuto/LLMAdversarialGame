def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    my_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                my_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                unclaimed.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    best = (-10**18, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**12
        else:
            val = 0
            if (nx, ny) in my_t:
                val += 3
            if (nx, ny) in opp_t:
                val += 7
            if (nx, ny) in unclaimed:
                val += 5
            # Prefer approaching center, but keep distance from opponent to avoid flip race
            val += -0.8 * (abs(nx - cx) + abs(ny - cy))
            val += -0.25 * (abs(nx - ox) + abs(ny - oy))
            # Safety: discourage stepping adjacent to opponent when not already ours
            adj_opp = (max(abs(nx - ox), abs(ny - oy)) == 1)
            if adj_opp and (nx, ny) not in my_t:
                val -= 3.5
            # Small bias to reduce oscillation: move that reduces manhattan to a rewarding cell if any
            if (observation.get("unclaimed_cells") or []) or (observation.get("opponent_territory") or []):
                tx, ty = ox, oy
                if unclaimed:
                    # deterministic closest unclaimed to us (scan order)
                    best_uc = None
                    best_d = 10**9
                    for x, y in unclaimed:
                        d = abs(x - sx) + abs(y - sy)
                        if d < best_d or (d == best_d and (x, y) < (best_uc[0], best_uc[1]) if best_uc else True):
                            best_d = d
                            best_uc = (x, y)
                    if best_uc:
                        tx, ty = best_uc
                val += -0.15 * (abs(nx - tx) + abs(ny - ty))
        if val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]