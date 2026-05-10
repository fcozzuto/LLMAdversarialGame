def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def parse_resources():
        out = []
        for r in observation.get("resources", []) or []:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict):
                pos = r.get("position", None)
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    out.append((int(pos[0]), int(pos[1])))
                elif "x" in r and "y" in r:
                    out.append((int(r["x"]), int(r["y"])))
        return out

    res = [p for p in parse_resources() if p not in obstacles]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_val = -10**9

    if not res:
        # drift toward opponent to block/contest
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # evaluate this move by best resource it would pursue, with opponent contest
        move_val = -10**9
        for tx, ty in res:
            sd = abs(tx - nx) + abs(ty - ny)
            od = abs(tx - ox) + abs(ty - oy)
            # prefer resources where we are closer than opponent; add mild tie-break to reduce self delay
            v = (od - sd) * 10 - sd
            # discourage stepping away from resources when opponent is already close
            if od <= 1 and sd > 1:
                v -= 50
            if v > move_val:
                move_val = v
        if move_val > best_val:
            best_val = move_val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]