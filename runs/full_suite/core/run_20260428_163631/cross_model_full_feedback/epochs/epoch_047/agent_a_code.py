def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y):
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obstacles:
            resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        a = ax - bx
        b = ay - by
        return a if a >= 0 else -a if b == 0 else (b if b >= 0 else -b if abs(a) <= abs(b) else abs(a))

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        ax = dx if dx >= 0 else -dx
        by = dy if dy >= 0 else -dy
        return ax if ax >= by else by

    opp = (ox, oy)
    us = (sx, sy)

    best = None
    best_val = None
    best_oppd = None

    # Deterministic move evaluation
    for dx, dy, nx, ny in legal:
        nxt = (nx, ny)
        # Base preference: get closer to reachable resource; discourage moves where opponent can steal earlier
        if resources:
            best_for_n = -10**9
            best_sd = -10**9
            for res in resources:
                usd = dist(nxt, res)
                opd = dist(opp, res)
                # If we are not worse, strongly prefer; if worse, still allow if opponent is far enough
                if usd <= opd:
                    val = 120 - 2 * usd + 0.6 * dist(opp, nxt)
                else:
                    val = 30 - 3 * (usd - opd) + 0.2 * dist(opp, nxt)
                # prefer resources that are closer to us even when tied
                if val > best_for_n or (val == best_for_n and (-usd) > best_sd):
                    best_for_n = val
                    best_sd = -usd
            val = best_for_n
        else:
            # No visible resources: drift toward center while staying away from opponent
            center = (w // 2, h // 2)
            val = -dist(nxt, center) + 0.5 * dist(opp, nxt)

        # Mild tie-breaks for determinism and to avoid jitter
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        val -= stay_pen * 2

        od = dist(nxt, opp)
        if best_val is None or val > best_val or (val == best_val and od > best_oppd) or (val == best_val and od == best_oppd and (dx, dy) < (best[0], best[1])):
            best_val = val
            best_oppd = od
            best = (dx, dy)

    return [int(best[0]), int(best[1])]