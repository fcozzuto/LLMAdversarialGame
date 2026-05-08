def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def best_target():
        if unclaimed:
            # nearest unclaimed, tie-break by lower y then x for determinism
            return min(unclaimed, key=lambda c: (abs(c[0]-sx) + abs(c[1]-sy), c[1], c[0]))
        return None

    tx = ty = None
    t = best_target()
    if t is not None:
        tx, ty = t[0], t[1]

    # subtle preference toward center if no unclaimed
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    tx2, ty2 = int(round(cx)), int(round(cy))

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0

        # hard avoid getting stuck on occupied opponent position
        if (nx, ny) == (ox, oy):
            val -= 1000000

        if (nx, ny) in self_terr:
            val += 25

        # prioritize capturing nearby unclaimed cells
        if (nx, ny) in unclaimed:
            val += 200000

        if tx is not None:
            d = abs(nx - tx) + abs(ny - ty)
            val += (500 - 20 * d)
        else:
            d = abs(nx - tx2) + abs(ny - ty2)
            val += (250 - 10 * d)

        # keep distance from opponent to resist being flipped back
        od = abs(nx - ox) + abs(ny - oy)
        val += (10 * od)

        # slight preference for progressing in dominant axis toward target to break ties
        if tx is not None:
            px = 0 if tx == sx else (1 if tx > sx else -1)
            py = 0 if ty == sy else (1 if ty > sy else -1)
            val += 3 if dx == px else 0
            val += 3 if dy == py else 0

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]